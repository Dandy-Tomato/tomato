package site.to_mato.auth.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record SignUpRequest(
        @Email @NotBlank String email,
        @NotBlank String password
) {}
