package site.to_mato.user.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.security.oauth.dto.OAuthUserInfo;
import site.to_mato.user.entity.OAuthAccount;
import site.to_mato.user.entity.User;
import site.to_mato.user.repository.OAuthAccountRepository;
import site.to_mato.user.repository.UserRepository;

@Service
@RequiredArgsConstructor
public class OAuthUserService {

    private final UserRepository userRepository;
    private final OAuthAccountRepository oAuthAccountRepository;

    @Transactional
    public User findOrCreate(OAuthUserInfo userInfo) {
        return oAuthAccountRepository
                .findByProviderAndProviderUserId(userInfo.getProvider(), userInfo.getProviderUserId())
                .map(OAuthAccount::getUser)
                .orElseGet(() -> {
                    User user = userRepository.save(User.createOAuth(userInfo.getEmail()));
                    OAuthAccount oAuthAccount = OAuthAccount.create(
                            user,
                            userInfo.getProvider(),
                            userInfo.getProviderUserId()
                    );
                    oAuthAccountRepository.save(oAuthAccount);
                    return user;
                });
    }
}
