package site.to_mato.topic.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.topic.dto.request.ReactionRequest;
import site.to_mato.topic.dto.response.BookmarkResponse;
import site.to_mato.topic.service.TopicBookmarkService;
import site.to_mato.topic.service.TopicReactionService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects/{projectId}/topics/{topicId}")
public class TopicActionController {

    private final TopicReactionService topicReactionService;
    private final TopicBookmarkService topicBookmarkService;

    @PostMapping("/reaction")
    public ApiResponse<Void> react(
            @PathVariable Long projectId,
            @PathVariable Long topicId,
            @RequestBody ReactionRequest request
    ) {
        topicReactionService.react(projectId, topicId, request.reaction(), request.version());
        return ApiResponse.ok(null);
    }

    @PostMapping("/bookmark")
    public ApiResponse<BookmarkResponse> bookmark(
            @PathVariable Long projectId,
            @PathVariable Long topicId
    ) {
        boolean isBookmarked = topicBookmarkService.toggleBookmark(projectId, topicId);
        return ApiResponse.ok(new BookmarkResponse(isBookmarked));
    }

}
