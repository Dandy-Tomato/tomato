package site.to_mato.project.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.common.response.PageResponse;
import site.to_mato.project.dto.response.MyProjectSummaryResponse;
import site.to_mato.project.dto.response.ProjectDetailResponse;
import site.to_mato.project.service.ProjectQueryService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects")
public class ProjectQueryController {

    private final ProjectQueryService projectQueryService;

    @GetMapping("/me")
    public ApiResponse<PageResponse<MyProjectSummaryResponse>> getMyProjects(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        Page<MyProjectSummaryResponse> result =
                projectQueryService.getMyProjects(userId, page, size);

        return ApiResponse.ok(PageResponse.from(result));
    }

    @GetMapping("/{projectId}")
    public ApiResponse<ProjectDetailResponse> getProjectDetail(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId
    ) {
        ProjectDetailResponse response = projectQueryService.getProjectDetail(userId, projectId);
        return ApiResponse.ok(response);
    }
}
