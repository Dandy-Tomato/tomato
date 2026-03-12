package site.to_mato.topic.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.topic.dto.request.ReactionRequest;
import site.to_mato.topic.service.TopicReactionService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects/{projectId}/topics/{topicId}")
public class TopicActionController {

    private final TopicReactionService topicReactionService;

    @PostMapping("/reaction")
    public ApiResponse<Void> react(
            @PathVariable Long projectId,
            @PathVariable Long topicId,
            @RequestBody ReactionRequest request
    ) {
        topicReactionService.react(projectId, topicId, request.reaction(), request.version());
        return ApiResponse.ok(null);
    }

}
