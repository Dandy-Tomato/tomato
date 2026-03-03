package site.to_mato.common.security.jwt;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@Validated
@ConfigurationProperties(prefix = "jwt")
public record JwtProperties(

        @NotBlank
        String secret,
        @NotNull
        Duration accessTokenTtl,
        @NotNull
        Duration refreshTokenTtl,
        @NotBlank
        String header,
        @NotBlank
        String prefix
) {}