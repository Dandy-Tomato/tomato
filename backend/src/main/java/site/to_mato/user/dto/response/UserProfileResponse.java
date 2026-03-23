package site.to_mato.user.dto.response;

import java.util.List;

public record UserProfileResponse(
        Long userId,
        String email,
        String nickname,
        String githubUsername,
        Long positionId,
        List<Long> skillIds,
        List<String> companyNames
) {
}
