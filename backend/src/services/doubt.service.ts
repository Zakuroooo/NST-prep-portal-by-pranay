/**
 * backend/src/services/doubt.service.ts
 * Business logic for student-side doubt thread operations.
 * Calls repositories only — never touches Mongoose directly.
 */

import { doubtRepository } from '../repositories/doubt.repository';
import { notificationRepository } from '../repositories/notification.repository';
import { facultyRepository } from '../repositories/faculty.repository';
import { ApiError } from '../utils/apiError';
import { sanitizeAndLimit, sanitizeText } from '../utils/sanitize';

export const doubtService = {
  /**
   * Get all doubt threads for a student (paginated).
   */
  async getStudentDoubts(studentId: string, page = 1, limit = 20) {
    return doubtRepository.findByStudentId(studentId, page, limit);
  },

  /**
   * Get a single doubt thread (validates ownership).
   */
  async getDoubtById(id: string, studentId: string) {
    const thread = await doubtRepository.findById(id);
    if (!thread) throw ApiError.notFound('Doubt thread not found.');

    if (thread.studentId.toString() !== studentId) {
      throw ApiError.forbidden('You do not have access to this doubt thread.');
    }

    return thread;
  },

  /**
   * Create a new doubt thread.
   * Sanitizes all text input before storage.
   */
  async createDoubt(
    studentId: string,
    studentName: string,
    data: {
      subject: string;
      body: string;
      tag: string;
      assignedFacultyId?: string;
    }
  ) {
    const sanitizedSubject = sanitizeAndLimit(data.subject, 300);
    const sanitizedBody = sanitizeAndLimit(data.body, 5000);

    if (!sanitizedSubject) throw ApiError.badRequest('Subject cannot be empty.');
    if (!sanitizedBody) throw ApiError.badRequest('Doubt body cannot be empty.');

    const thread = await doubtRepository.create({
      studentId: studentId as never,
      studentName,
      subject: sanitizedSubject,
      body: sanitizedBody,
      tag: data.tag as never,
      status: 'pending',
      assignedFacultyId: data.assignedFacultyId as never,
      replies: [],
    });

    // Notify assigned faculty if provided
    if (data.assignedFacultyId) {
      notificationRepository
        .create({
          userId: data.assignedFacultyId,
          type: 'doubt',
          title: 'New doubt assigned to you',
          subtitle: `${studentName}: ${sanitizedSubject.slice(0, 80)}`,
          iconName: 'HelpCircle',
        })
        .catch(() => {}); // non-blocking
    }

    return thread;
  },

  /**
   * Add a reply from a student to their own thread.
   */
  async addStudentReply(
    doubtId: string,
    studentId: string,
    studentName: string,
    body: string
  ) {
    const thread = await doubtRepository.findById(doubtId);
    if (!thread) throw ApiError.notFound('Doubt thread not found.');

    if (thread.studentId.toString() !== studentId) {
      throw ApiError.forbidden('You do not have permission to reply to this thread.');
    }

    if (thread.status === 'resolved') {
      throw ApiError.badRequest('Cannot reply to a resolved thread.');
    }

    const sanitizedBody = sanitizeAndLimit(body, 5000);
    if (!sanitizedBody) throw ApiError.badRequest('Reply body cannot be empty.');

    return doubtRepository.addReply(doubtId, {
      authorId: studentId,
      authorName: studentName,
      authorRole: 'student',
      body: sanitizedBody,
    });
  },

  /**
   * Mark a doubt thread as resolved by the student.
   */
  async resolveDoubt(doubtId: string, studentId: string) {
    const thread = await doubtRepository.findById(doubtId);
    if (!thread) throw ApiError.notFound('Doubt thread not found.');

    if (thread.studentId.toString() !== studentId) {
      throw ApiError.forbidden('You do not have permission to resolve this thread.');
    }

    return doubtRepository.updateStatus(doubtId, 'resolved');
  },
};
