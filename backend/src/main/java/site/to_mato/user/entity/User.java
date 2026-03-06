package site.to_mato.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.SQLDelete;
import site.to_mato.catalog.entity.Position;
import site.to_mato.common.entity.SoftDeleteEntity;
import site.to_mato.user.entity.enums.Role;

@Getter
@Entity
@Table(name = "users")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@SQLDelete(sql = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ?")
public class User extends SoftDeleteEntity {

    @Id
    @Column(name = "user_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, length = 255)
    private String email;

    @Column(length = 255)
    private String password;

    @Column(length = 50)
    private String nickname;

    @Column(length = 255)
    private String githubUsername;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Role role;

    @Column(name = "is_onboarding", nullable = false)
    private boolean isOnboarding;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "position_id")
    private Position position;

    @Builder(access = AccessLevel.PRIVATE)
    private User(String email, String password, String nickname,
                 Role role, boolean isOnboarding, Position position) {
        this.email = email;
        this.password = password;
        this.nickname = nickname;
        this.role = role;
        this.isOnboarding = isOnboarding;
        this.position = position;
    }

    // 일반 회원가입
    public static User createLocal(String email, String encodedPassword) {
        return User.builder()
                .email(email)
                .password(encodedPassword)
                .role(Role.ROLE_USER)
                .isOnboarding(false)
                .build();
    }

    // OAuth 회원가입
    public static User createSocial(String email) {
        return User.builder()
                .email(email)
                .role(Role.ROLE_USER)
                .isOnboarding(false)
                .build();
    }

    // 온보딩 완료
    public void updateProfile(String nickname, String githubUsername, Position position) {
        this.nickname = nickname;
        this.githubUsername = githubUsername;
        this.position = position;
        this.isOnboarding = true;
    }
}