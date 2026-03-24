package site.to_mato.project.dto.response;

import site.to_mato.project.entity.enums.ProjectRole;

public record ProjectMemberResponse(
        Long userId,
        String nickname,
        ProjectRole projectRole,
        Long positionId
) {
    public static ProjectMemberResponse of(
            Long userId,
            String nickname,
            ProjectRole projectRole,
            Long positionId
    ) {
        return new ProjectMemberResponse(userId, nickname, projectRole, positionId);
    }
}
