package site.to_mato.project.dto.response;

import site.to_mato.project.entity.enums.ProjectRole;

import java.time.LocalDate;

public record MyProjectSummaryResponse(
        Long projectId,
        String name,
        ProjectRole projectRole,
        boolean topicState,
        long memberCount,
        LocalDate startedAt,
        LocalDate dueAt
) {
    public static MyProjectSummaryResponse of(
            Long projectId,
            String name,
            ProjectRole projectRole,
            boolean topicState,
            long memberCount,
            LocalDate startedAt,
            LocalDate dueAt
    ) {
        return new MyProjectSummaryResponse(
                projectId,
                name,
                projectRole,
                topicState,
                memberCount,
                startedAt,
                dueAt
        );
    }
}
