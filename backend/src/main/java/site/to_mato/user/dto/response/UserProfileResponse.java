package site.to_mato.user.dto.response;

import java.util.List;

public record UserProfileResponse(
        String email,
        String nickname,
        String githubUsername,
        Long position,
        List<Long> skillIds,
        List<Long> companyIds
) {

    public static UserProfileResponse of(
            String email,
            String nickname,
            String githubUsername,
            Long position,
            List<Long> skillIds,
            List<Long> companyIds
    ) {
        return new UserProfileResponse(
                email,
                nickname,
                githubUsername,
                position,
                skillIds,
                companyIds
        );
    }
}
