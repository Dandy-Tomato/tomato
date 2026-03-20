package site.to_mato.project.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record JoinProjectRequest(
        @NotBlank
        @Size(min = 8, max = 8)
        String inviteCode
) {
}
