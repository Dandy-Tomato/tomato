package site.to_mato.project.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.project.dto.request.CreateProjectRequest;
import site.to_mato.project.dto.request.JoinProjectRequest;
import site.to_mato.project.dto.request.UpdateProjectRequest;
import site.to_mato.project.dto.response.ProjectIdResponse;
import site.to_mato.project.dto.response.ProjectInviteCodeResponse;
import site.to_mato.project.service.ProjectService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects")
public class ProjectController {

    private final ProjectService projectService;

    @PostMapping
    public ApiResponse<ProjectIdResponse> createProject(
            @Valid @RequestBody CreateProjectRequest request,
            @AuthenticationPrincipal Long userId
    ) {
        ProjectIdResponse response = projectService.createProject(userId, request);

        return ApiResponse.ok(response);
    }

    @PatchMapping("/{projectId}")
    public ApiResponse<ProjectIdResponse> updateProject(
            @PathVariable Long projectId,
            @AuthenticationPrincipal Long userId,
            @RequestBody UpdateProjectRequest request
    ) {
        ProjectIdResponse response = projectService.updateProject(userId, projectId, request);
        return ApiResponse.ok(response);
    }

    @DeleteMapping("/{projectId}")
    public ApiResponse<ProjectIdResponse> deleteProject(
            @PathVariable Long projectId,
            @AuthenticationPrincipal Long userId
    ) {
        ProjectIdResponse response = projectService.deleteProject(userId, projectId);
        return ApiResponse.ok(response);
    }

    @GetMapping("/{projectId}/invite-code")
    public ApiResponse<ProjectInviteCodeResponse> getProjectInviteCode(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId
    ) {
        ProjectInviteCodeResponse response = projectService.getProjectInviteCode(userId, projectId);
        return ApiResponse.ok(response);
    }

    @PostMapping("/join")
    public ApiResponse<ProjectIdResponse> joinProject(
            @AuthenticationPrincipal Long userId,
            @RequestBody JoinProjectRequest request
    ) {
        ProjectIdResponse response = projectService.joinProject(userId, request);
        return ApiResponse.ok(response);
    }

    @DeleteMapping("/{projectId}/members")
    public ApiResponse<ProjectIdResponse> leaveProject(
            @PathVariable Long projectId,
            @AuthenticationPrincipal Long userId
    ) {
        ProjectIdResponse response = projectService.leaveProject(userId, projectId);
        return ApiResponse.ok(response);
    }
}
