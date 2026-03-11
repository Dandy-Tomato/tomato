package site.to_mato.user.entity.enums;

import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;

import java.util.Arrays;

public enum OAuthProvider {
    GOOGLE,
    GITHUB;

    public static OAuthProvider from(String registrationId) {
        return Arrays.stream(values())
                .filter(provider -> provider.name().equalsIgnoreCase(registrationId))
                .findFirst()
                .orElseThrow(() -> new BusinessException(ErrorCode.OAUTH_PROVIDER_NOT_SUPPORTED));
    }
}
