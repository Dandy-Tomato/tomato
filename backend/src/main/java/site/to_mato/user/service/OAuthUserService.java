package site.to_mato.user.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.UserRepository;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class OAuthUserService {

    private final UserRepository userRepository;

    @Transactional
    public User findOrCreate(String provider, Map<String, Object> attr) {
        String providerId = String.valueOf(attr.get("id"));
        String login = (String) attr.get("login");
        String email = (String) attr.get("email");

        return userRepository.findByProviderAndProviderId(provider, providerId)
                .orElseGet(() -> userRepository.save(
                        User.createOAuth(provider, providerId, login, email)
                ));
    }
}