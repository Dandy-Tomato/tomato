package site.to_mato.user.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Skill;

@Getter
@Entity
@Table(
        name = "user_skills",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_user_skill",
                        columnNames = {"user_id", "skill_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class UserSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_skill_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id")
    private User user;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "skill_id")
    private Skill skill;

    @Builder
    private UserSkill(User user, Skill skill) {
        this.user = user;
        this.skill = skill;
    }

    public static UserSkill of(User user, Skill skill) {
        return UserSkill.builder()
                .user(user)
                .skill(skill)
                .build();
    }
}