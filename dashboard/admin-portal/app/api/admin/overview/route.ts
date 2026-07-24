/**
 * dashboard/admin-portal/app/api/admin/overview/route.ts
 * GET /api/admin/overview — platform-wide KPIs.
 *
 * Architecture: Route → Service → Repository → DB
 */

import { NextRequest, NextResponse } from 'next/server';
import connectDB from 'placeprep-backend/src/config/db';
import { requireAdmin } from 'placeprep-backend/src/utils/authMiddleware';
import { adminService } from 'placeprep-backend/src/services/admin.service';
import { successResponse } from 'placeprep-backend/src/utils/apiResponse';
import { handleApiError } from 'placeprep-backend/src/utils/apiError';

export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    await connectDB();
    await requireAdmin(request);
    const data = await adminService.getOverview();
    return successResponse(data);
  } catch (error) {
    return handleApiError(error);
  }
}
