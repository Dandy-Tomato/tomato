package site.to_mato.project.dto.response;

import java.time.LocalDate;
import java.util.List;

public record ProjectDetailResponse(
        Long projectId,
        String name,
        String description,
        LocalDate startedAt,
        LocalDate dueAt,
        String inviteCode,
        boolean topicState,
        ProjectOwnerResponse owner,
        List<Long> domains,
        long memberCount,
        List<ProjectMemberResponse> members
) {
    public static ProjectDetailResponse of(
            Long projectId,
            String name,
            String description,
            LocalDate startedAt,
            LocalDate dueAt,
            String inviteCode,
            boolean topicState,
            ProjectOwnerResponse owner,
            List<Long> domains,
            long memberCount,
            List<ProjectMemberResponse> members
    ) {
        return new ProjectDetailResponse(
                projectId,
                name,
                description,
                startedAt,
                dueAt,
                inviteCode,
                topicState,
                owner,
                domains,
                memberCount,
                members
        );
    }
}
