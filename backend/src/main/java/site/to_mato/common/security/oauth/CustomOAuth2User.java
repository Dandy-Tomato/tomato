package site.to_mato.common.security.oauth;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.Collection;
import java.util.List;
import java.util.Map;

public record CustomOAuth2User(
        Long userId,
        String role,
        boolean isOnboarding,
        Map<String, Object> attributes
) implements OAuth2User {

    public static CustomOAuth2User of(
            Long userId,
            String role,
            boolean isOnboarding,
            Map<String, Object> attributes
    ) {
        return new CustomOAuth2User(userId, role, isOnboarding, attributes);
    }

    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority(role));
    }

    @Override
    public String getName() {
        return String.valueOf(userId);
    }
}
