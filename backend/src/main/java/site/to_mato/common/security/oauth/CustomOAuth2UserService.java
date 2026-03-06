package site.to_mato.common.security.oauth;

import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.common.security.oauth.dto.OAuthUserInfo;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.enums.OAuthProvider;
import site.to_mato.user.service.OAuthUserService;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    private final OAuthUserService oAuthUserService;

    @Override
    @Transactional
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(userRequest);

        String registrationId = userRequest.getClientRegistration().getRegistrationId();
        OAuthProvider provider = OAuthProvider.from(registrationId);

        Map<String, Object> attributes = oAuth2User.getAttributes();
        OAuthUserInfo userInfo = extractOAuthUserInfo(provider, attributes);

        User user = oAuthUserService.findOrCreate(userInfo);

        return CustomOAuth2User.of(
                user.getId(),
                user.getRole().name(),
                user.isOnboarding(),
                attributes
        );
    }

    private OAuthUserInfo extractOAuthUserInfo(OAuthProvider provider, Map<String, Object> attributes) {
        if (provider == OAuthProvider.GITHUB) {
            return OAuthUserInfo.builder()
                    .provider(provider)
                    .providerUserId(String.valueOf(attributes.get("id")))
                    .email((String) attributes.get("email"))
                    .build();
        }

        if (provider == OAuthProvider.GOOGLE) {
            return OAuthUserInfo.builder()
                    .provider(provider)
                    .providerUserId(String.valueOf(attributes.get("sub")))
                    .email((String) attributes.get("email"))
                    .build();
        }

        throw new BusinessException(ErrorCode.OAUTH_PROVIDER_NOT_SUPPORTED);
    }
}
