package site.to_mato.project.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.project.dto.request.ReactionRequest;
import site.to_mato.project.dto.response.BookmarkResponse;
import site.to_mato.project.dto.response.ProjectTopicReactionResponse;
import site.to_mato.project.service.ProjectTopicBookmarkService;
import site.to_mato.project.service.ProjectTopicReactionService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects/{projectId}/topics/{topicId}")
public class ProjectTopicActionController {

    private final ProjectTopicReactionService projectTopicReactionService;
    private final ProjectTopicBookmarkService projectTopicBookmarkService;

    @PostMapping("/reaction")
    public ApiResponse<ProjectTopicReactionResponse> setReaction(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @PathVariable Long topicId,
            @RequestBody ReactionRequest request
    ) {
        ProjectTopicReactionResponse response =
                projectTopicReactionService.setReaction(userId, projectId, topicId, request);

        return ApiResponse.ok(response);
    }

    @PostMapping("/bookmark")
    public ApiResponse<BookmarkResponse> toggleBookmark(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @PathVariable Long topicId
    ) {
        boolean isBookmarked = projectTopicBookmarkService.toggleBookmark(userId, projectId, topicId);
        return ApiResponse.ok(new BookmarkResponse(isBookmarked));
    }

}
