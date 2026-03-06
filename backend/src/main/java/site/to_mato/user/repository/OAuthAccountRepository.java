package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.user.entity.OAuthAccount;
import site.to_mato.user.entity.enums.OAuthProvider;

import java.util.Optional;

public interface OAuthAccountRepository extends JpaRepository<OAuthAccount, Long> {

    Optional<OAuthAccount> findByProviderAndProviderUserId(OAuthProvider provider, String providerUserId);
}
