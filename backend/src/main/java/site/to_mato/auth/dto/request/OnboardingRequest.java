package site.to_mato.auth.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public record OnboardingRequest(
        @NotBlank String nickname,
        String githubUsername,
        @NotNull Long positionId,
        @NotEmpty List<Long> companyIds,
        @NotEmpty List<Long> skillIds
) {}