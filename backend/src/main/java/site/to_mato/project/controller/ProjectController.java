package site.to_mato.project.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.project.dto.request.CreateProjectRequest;
import site.to_mato.project.dto.response.CreateProjectResponse;
import site.to_mato.project.service.ProjectService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects")
public class ProjectController {

    private final ProjectService projectService;

    @PostMapping
    public ApiResponse<CreateProjectResponse> createProject(
            @Valid @RequestBody CreateProjectRequest request,
            @AuthenticationPrincipal Long userId
    ) {
        CreateProjectResponse response = projectService.createProject(userId, request);

        return ApiResponse.ok(response);
    }
}