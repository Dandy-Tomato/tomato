package site.to_mato.common.security.oauth.dto;

import lombok.Builder;
import lombok.Getter;
import site.to_mato.user.entity.enums.OAuthProvider;

@Getter
@Builder
public class OAuthUserInfo {

    private final OAuthProvider provider;
    private final String providerUserId;
    private final String email;
}
