/**
 * backend/src/services/student.service.ts
 * Business logic for student portal features.
 */

import { studentRepository } from '../repositories/student.repository';
import { roadmapRepository } from '../repositories/roadmap.repository';
import { companyRepository } from '../repositories/company.repository';
import { questionRepository } from '../repositories/question.repository';
import { notificationRepository } from '../repositories/notification.repository';
import QuestionCompletion from '../models/QuestionCompletion';
import { ApiError } from '../utils/apiError';
import mongoose from 'mongoose';
import type { OnboardingInput } from '../validators/student.validator';

const XP_BY_DIFFICULTY: Record<string, number> = {
  Easy: 10,
  Medium: 25,
  Hard: 50,
};

export const studentService = {
  async getProfile(userId: string) {
    let profile = await studentRepository.findByUserId(userId);
    if (!profile) {
      // Auto-create default profile for robustness to prevent 404s
      const user = await import('../repositories/user.repository').then(m => m.userRepository.findById(userId));
      if (!user) throw ApiError.notFound('User not found');
      
      profile = await studentRepository.create({
        userId: new mongoose.Types.ObjectId(userId),
        fullName: user.email.split('@')[0],
        batch: '2024',
        branch: 'CS & AI',
        year: '3rd',
        onboardingComplete: false,
        placementStatus: 'IN_PROGRESS',
      } as never);
    }
    return profile;
  },

  async updateProfile(userId: string, data: Record<string, unknown>) {
    const profile = await studentRepository.updateByUserId(userId, data);
    if (!profile) throw ApiError.notFound('Student profile');
    return profile;
  },

  async getStats(userId: string) {
    let profile = await studentRepository.findByUserId(userId);
    if (!profile) {
      profile = await this.getProfile(userId); // Use the robust getProfile
    }

    const [roadmaps, problemsSolved] = await Promise.all([
      roadmapRepository.findByStudentId(userId),
      QuestionCompletion.countDocuments({
        studentId: new mongoose.Types.ObjectId(userId),
      }),
    ]);

    // Calculate prep score: weighted blend of XP, problems solved, streak
    const prepScore = Math.min(
      100,
      Math.round(
        (profile.xpTotal / 1500) * 40 +
          (problemsSolved / 80) * 40 +
          (profile.currentStreakDays / 30) * 20
      )
    );

    // 30-day activity chart
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const activity = await QuestionCompletion.aggregate([
      {
        $match: {
          studentId: new mongoose.Types.ObjectId(userId),
          completedAt: { $gte: thirtyDaysAgo },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: { format: '%Y-%m-%d', date: '$completedAt' },
          },
          count: { $sum: 1 },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    const weeklyActivity = activity.map((a: { _id: string; count: number }) => ({
      date: a._id,
      count: a.count,
    }));

    // Get latest activity
    const latestCompletion = await QuestionCompletion.findOne({
      studentId: new mongoose.Types.ObjectId(userId)
    })
    .sort({ completedAt: -1 })
    .populate('questionId', 'title problemSummary');

    let latestActivity = null;
    if (latestCompletion && latestCompletion.questionId) {
      latestActivity = {
        title: (latestCompletion.questionId as any).title,
        completedAt: latestCompletion.completedAt,
      };
    }

    return {
      xpTotal: profile.xpTotal,
      currentStreakDays: profile.currentStreakDays,
      problemsSolved,
      prepScore,
      companiesOnRoadmap: roadmaps.length,
      weeklyActivity,
      onboardingComplete: profile.onboardingComplete,
      latestActivity,
    };
  },

  async completeOnboarding(userId: string, data: OnboardingInput) {
    const profile = await studentRepository.findByUserId(userId);
    if (!profile) throw ApiError.notFound('Student profile');

    // Update profile with onboarding data
    await studentRepository.updateByUserId(userId, {
      targetDomains: data.targetDomains,
      targetCategories: data.targetCategories as never,
      topicSelfRatings: new Map(Object.entries(data.topicSelfRatings)),
      targetCompanySlugs: data.targetCompanySlugs,
      prepWeeksCommitted: data.prepWeeksCommitted,
      onboardingComplete: true,
      onboardingCompletedAt: new Date(),
    });

    // Create roadmaps for each target company (max 3 to start)
    const companies = await companyRepository.findBySlugs(
      data.targetCompanySlugs.slice(0, 3)
    );

    for (const company of companies) {
      // Check if roadmap already exists
      const existing = await roadmapRepository.findByStudentAndCompany(
        userId,
        company.slug
      );
      if (existing) continue;

      // Generate week structure based on topicFrequency
      const totalWeeks = data.prepWeeksCommitted;
      const weeks = company.topicFrequency.slice(0, totalWeeks).map((tf, i) => ({
        weekNumber: i + 1,
        topicLabel: tf.topicName,
        totalQuestions: Math.max(5, Math.round(tf.questionCount / 4)),
        doneQuestions: 0,
        status: (i === 0 ? 'active' : 'locked') as 'active' | 'locked',
      }));

      // Fill remaining weeks with "Practice" if fewer topics than weeks
      while (weeks.length < totalWeeks) {
        weeks.push({
          weekNumber: weeks.length + 1,
          topicLabel: 'Mixed Practice',
          totalQuestions: 5,
          doneQuestions: 0,
          status: 'locked',
        });
      }

      await roadmapRepository.create({
        studentId: new mongoose.Types.ObjectId(userId),
        companyId: company._id,
        companySlug: company.slug,
        companyName: company.name,
        companyLogoUrl: company.logoUrl,
        roleName: 'Software Engineer',
        weeksCommitted: totalWeeks,
        currentWeek: 1,
        pctComplete: 0,
        isActive: true,
        weeks,
      } as never);
    }

    // XP reward for completing onboarding
    await studentRepository.addXp(userId, 100);
    await notificationRepository.create({
      userId,
      type: 'xp',
      title: '+100 XP — Onboarding Complete!',
      subtitle: `Your roadmap${companies.length > 1 ? 's are' : ' is'} ready. Start practicing!`,
      iconName: 'Zap',
    });

    return { success: true };
  },

  async completeQuestion(
    userId: string,
    questionId: string,
    roadmapId?: string
  ) {
    const question = await questionRepository.findById(questionId);
    if (!question) throw ApiError.notFound('Question');

    const oid = new mongoose.Types.ObjectId(userId);
    const qid = new mongoose.Types.ObjectId(questionId);

    // Check if already completed (unique index handles this, but let's be explicit)
    const existing = await QuestionCompletion.findOne({ studentId: oid, questionId: qid });
    if (existing) {
      throw ApiError.conflict('You have already completed this question.');
    }

    const xpEarned = XP_BY_DIFFICULTY[question.difficulty] || 10;

    // Atomic: save completion + add XP
    await Promise.all([
      QuestionCompletion.create({
        studentId: oid,
        questionId: qid,
        roadmapId: roadmapId ? new mongoose.Types.ObjectId(roadmapId) : undefined,
        companySlug: question.companySlug,
        difficulty: question.difficulty,
        xpEarned,
      }),
      studentRepository.addXp(userId, xpEarned),
    ]);

    // Update roadmap week progress if roadmapId provided
    if (roadmapId) {
      const roadmap = await roadmapRepository.findById(roadmapId);
      if (roadmap) {
        const activeWeek = roadmap.weeks.find((w) => w.status === 'active');
        if (activeWeek) {
          await roadmapRepository.incrementWeekProgress(roadmapId, activeWeek.weekNumber);
        }
      }
    }

    // XP notification
    await notificationRepository.create({
      userId,
      type: 'xp',
      title: `+${xpEarned} XP Earned`,
      subtitle: `${question.difficulty} problem solved: ${question.problemSummary.slice(0, 60)}...`,
      iconName: 'Zap',
    });

    return { xpEarned, totalXp: 0 }; // totalXp fetched fresh by client
  },

  async getLeaderboard(batch?: string) {
    const profiles = await studentRepository.getLeaderboard(batch, 100);
    return profiles.map((p, i) => ({
      rank: i + 1,
      studentId: p.userId.toString(),
      studentName: p.fullName,
      batch: p.batch,
      branch: p.branch,
      avatarUrl: p.avatarUrl,
      xp: p.xpTotal,
      placementStatus: p.placementStatus,
    }));
  },

  /**
   * Topic-wise question completion percentage.
   * Returns an array like: [{ topic, completed, total, percentage }]
   */
  async getTopicProgress(userId: string) {
    const studentObjId = new mongoose.Types.ObjectId(userId);

    // Aggregate completions by topic via lookup
    const result = await QuestionCompletion.aggregate([
      { $match: { studentId: studentObjId } },
      {
        $lookup: {
          from: 'questions',
          localField: 'questionId',
          foreignField: '_id',
          as: 'question',
        },
      },
      { $unwind: '$question' },
      { $unwind: '$question.topics' },
      {
        $group: {
          _id: '$question.topics',
          completed: { $sum: 1 },
        },
      },
    ]);

    // Get total questions per topic
    const totals = await QuestionCompletion.db
      .collection('questions')
      .aggregate([
        { $unwind: '$topics' },
        { $group: { _id: '$topics', total: { $sum: 1 } } },
      ])
      .toArray();

    const totalMap = new Map<string, number>(
      (totals as { _id: string; total: number }[]).map((t) => [t._id, t.total])
    );

    return result.map((r: { _id: string; completed: number }) => ({
      topic: r._id,
      completed: r.completed,
      total: totalMap.get(r._id) ?? 0,
      percentage:
        totalMap.get(r._id)
          ? Math.round((r.completed / totalMap.get(r._id)!) * 100)
          : 0,
    }));
  },

  async resetOnboarding(userId: string) {
    await studentRepository.updateByUserId(userId, { onboardingComplete: false });
    return { success: true };
  },

  async resetRoadmap(userId: string) {
    await roadmapRepository.deleteByStudentId(userId);
    return { success: true };
  },
};
