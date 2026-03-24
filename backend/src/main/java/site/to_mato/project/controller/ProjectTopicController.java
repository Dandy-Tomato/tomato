package site.to_mato.project.controller;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.project.dto.request.ConfirmProjectTopicRequest;
import site.to_mato.project.dto.response.ConfirmedProjectTopicResponse;
import site.to_mato.project.service.ProjectTopicService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects")
public class ProjectTopicController {

    private final ProjectTopicService projectTopicService;

    @PutMapping("/{projectId}/confirmed-topic")
    public ApiResponse<ConfirmedProjectTopicResponse> confirmProjectTopic(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @Valid @RequestBody ConfirmProjectTopicRequest request
    ) {
        ConfirmedProjectTopicResponse response = projectTopicService.confirmProjectTopic(userId, projectId, request);
        return ApiResponse.ok(response);
    }

    @DeleteMapping("/{projectId}/confirmed-topic")
    public ApiResponse<ConfirmedProjectTopicResponse> clearConfirmedProjectTopic(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId
    ) {
        ConfirmedProjectTopicResponse response = projectTopicService.clearConfirmedProjectTopic(userId, projectId);
        return ApiResponse.ok(response);
    }
}