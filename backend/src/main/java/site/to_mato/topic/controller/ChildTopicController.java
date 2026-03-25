package site.to_mato.topic.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import site.to_mato.common.response.ApiResponse;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import site.to_mato.topic.dto.response.ChildTopicDetailResponse;
import site.to_mato.topic.dto.response.RefinedTopicResponse;
import site.to_mato.topic.service.ChildTopicService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects/{projectId}")
public class ChildTopicController {
    private final ChildTopicService childTopicService;

    @PostMapping("/refine/{topicId}")
    public ApiResponse<RefinedTopicResponse> refineTopic(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @PathVariable Long topicId
    ) {
        RefinedTopicResponse response = childTopicService.refineTopic(userId, projectId, topicId);
        return ApiResponse.ok(response);
    }

    @PostMapping("/refine/mock")
    public ApiResponse<String> refineTopic(
    ) {
        String response = childTopicService.refineMockTopic();
        return ApiResponse.ok(response);
    }

    @GetMapping("/child-topics/{childTopicId}")
    public ApiResponse<ChildTopicDetailResponse> getChildTopic(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @PathVariable Long childTopicId
    ) {
        ChildTopicDetailResponse response = childTopicService.getChildTopic(userId, projectId, childTopicId);
        return ApiResponse.ok(response);
    }

    @DeleteMapping("/child-topics/{childTopicId}")
    public ApiResponse<Void> deleteChildTopic(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @PathVariable Long childTopicId
    ) {
        childTopicService.deleteChildTopic(userId, projectId, childTopicId);
        return ApiResponse.ok(null);
    }

}
