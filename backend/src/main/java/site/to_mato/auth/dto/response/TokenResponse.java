package site.to_mato.auth.dto.response;

public record TokenResponse(
        Long userId,
        String accessToken,
        String refreshToken
) {

    public static TokenResponse of(Long userId, String accessToken, String refreshToken) {
        return new TokenResponse(userId, accessToken, refreshToken);
    }
}
