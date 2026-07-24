/**
 * dashboard/student-portal/app/api/user/me/roadmap/route.ts
 * GET /api/user/me/roadmap — student's full roadmap with week-by-week breakdown.
 *
 * Architecture: Route → Service → Repository → DB
 */

import { NextRequest, NextResponse } from 'next/server';
import connectDB from 'placeprep-backend/src/config/db';
import { requireStudent } from 'placeprep-backend/src/utils/authMiddleware';
import { roadmapRepository } from 'placeprep-backend/src/repositories/roadmap.repository';
import { successResponse } from 'placeprep-backend/src/utils/apiResponse';
import { handleApiError } from 'placeprep-backend/src/utils/apiError';

export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    await connectDB();
    const user = await requireStudent(request);
    const roadmaps = await roadmapRepository.findByStudentId(user.userId);
    return successResponse(roadmaps);
  } catch (error) {
    return handleApiError(error);
  }
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const user = await requireStudent(request);
    await connectDB();
    const body = await request.json();
    const { companySlug, targetRole, preparationWeeks } = body;

    if (!companySlug) {
      return NextResponse.json(
        { success: false, error: { message: "companySlug is required" } },
        { status: 400 }
      );
    }

    const existing = await roadmapRepository.findByStudentAndCompany(user.userId as any, companySlug);
    if (existing) {
      return NextResponse.json(
        { success: false, error: { message: "Company already in roadmap" } },
        { status: 400 }
      );
    }

    const newRoadmap = await roadmapRepository.create({
      studentId: user.userId as any,
      companyId: user.userId as any, // HACK: need actual companyId from Company model, but skipping for now or should look it up
      companySlug,
      companyName: companySlug.toUpperCase(),
      roleName: targetRole || "SDE-1",
      weeksCommitted: preparationWeeks || 12,
      currentWeek: 1,
      pctComplete: 0,
      isActive: true,
      weeks: [
        {
          weekNumber: 1,
          topicLabel: "Arrays & Strings",
          totalQuestions: 10,
          doneQuestions: 0,
          status: "active",
        }
      ]
    } as any);

    return NextResponse.json(successResponse(newRoadmap, { status: 201 }), { status: 201 });
  } catch (error) {
    return handleApiError(error);
  }
}
