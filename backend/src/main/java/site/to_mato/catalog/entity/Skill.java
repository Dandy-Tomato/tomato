package site.to_mato.catalog.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table(name = "skills")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Skill {

    @Id
    @Column(name = "skill_id")
    private Long id;

    @Column(name = "name", nullable = false, unique = true, length = 100)
    private String name;

    @Builder
    public Skill(Long id, String name) {
        this.id = id;
        this.name = name;
    }
}
