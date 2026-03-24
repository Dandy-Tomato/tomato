package site.to_mato.project.dto.response;

public record ProjectInviteCodeResponse(
        Long projectId,
        String inviteCode
) {

    public static ProjectInviteCodeResponse of(Long projectId, String inviteCode) {
        return new ProjectInviteCodeResponse(projectId, inviteCode);
    }
}
