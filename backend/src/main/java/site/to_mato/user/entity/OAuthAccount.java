package site.to_mato.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.common.entity.BaseEntity;
import site.to_mato.user.entity.enums.OAuthProvider;

@Getter
@Entity
@Table(
        name = "oauth_accounts",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_oauth_provider_user",
                        columnNames = {"provider", "provider_user_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class OAuthAccount extends BaseEntity {

    @Id
    @Column(name = "oauth_account_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "provider", nullable = false, length = 20)
    private OAuthProvider provider;

    @Column(name = "provider_user_id", nullable = false, length = 100)
    private String providerUserId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Builder(access = AccessLevel.PRIVATE)
    private OAuthAccount(User user, OAuthProvider provider, String providerUserId) {
        this.user = user;
        this.provider = provider;
        this.providerUserId = providerUserId;
    }

    public static OAuthAccount of(User user, OAuthProvider provider, String providerUserId) {
        return OAuthAccount.builder()
                .user(user)
                .provider(provider)
                .providerUserId(providerUserId)
                .build();
    }
}
