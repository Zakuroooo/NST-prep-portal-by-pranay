/**
 * dashboard/student-portal/app/api/auth/me/route.ts
 * GET /api/auth/me — returns current user from JWT cookie.
 */

import { NextRequest, NextResponse } from 'next/server';
import connectDB from 'placeprep-backend/src/config/db';
import { requireAuth } from 'placeprep-backend/src/utils/authMiddleware';
import { studentRepository } from 'placeprep-backend/src/repositories/student.repository';
import { successResponse } from 'placeprep-backend/src/utils/apiResponse';
import { handleApiError } from 'placeprep-backend/src/utils/apiError';

export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    await connectDB();
    const user = await requireAuth(request, 'student');
    const profile = await studentRepository.findByUserId(user.userId);

    return successResponse({
      userId: user.userId,
      role: user.role,
      email: user.email,
      fullName: profile?.fullName,
      studentId: profile?.studentId,
      branch: profile?.branch,
      batch: profile?.batch,
      bio: profile?.bio,
      linkedinUrl: profile?.linkedinUrl,
      githubUrl: profile?.githubUrl,
      xpTotal: profile?.xpTotal,
      rank: profile?.rank,
      currentStreakDays: profile?.currentStreakDays,
      solved: profile?.solved,
      targetCategories: profile?.targetCategories,
      onboardingComplete: profile?.onboardingComplete ?? false,
      placementStatus: profile?.placementStatus,
      avatarUrl: profile?.avatarUrl,
    });
  } catch (error) {
    return handleApiError(error);
  }
}
