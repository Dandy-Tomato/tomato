package site.to_mato.user.dto.response;

import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class UserProfileResponse {

    private String nickname;
    private String githubUsername;
    private Long position;
    private List<Long> skillIds;
    private List<Long> companyIds;
}