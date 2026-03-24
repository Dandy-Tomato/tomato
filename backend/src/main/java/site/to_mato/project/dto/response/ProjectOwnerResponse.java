package site.to_mato.project.dto.response;

public record ProjectOwnerResponse(
        Long userId,
        String nickname
) {
    public static ProjectOwnerResponse of(Long userId, String nickname) {
        return new ProjectOwnerResponse(userId, nickname);
    }
}
