package site.to_mato.auth.dto.request;

import jakarta.validation.constraints.NotBlank;

import java.util.List;

public record OnboardingRequest(
        @NotBlank String nickname,
        String githubUsername,
        Long positionId,
        List<Long> companyIds,
        List<Long> skillIds
) {}
