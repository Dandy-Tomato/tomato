package site.to_mato.project.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Skill;

@Getter
@Entity
@Table(
        name = "project_skills",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_project_skill",
                        columnNames = {"project_id", "skill_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProjectSkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_skill_id")
    private Long id;

    @Column(name = "weight")
    private double weight;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "skill_id", nullable = false)
    private Skill skill;

    @Builder(access = AccessLevel.PRIVATE)
    private ProjectSkill(
            Project project,
            Skill skill,
            double weight
    ) {
        this.project = project;
        this.skill = skill;
        this.weight = weight;
    }

    public static ProjectSkill of(Project project, Skill skill, double weight) {
        return ProjectSkill.builder()
                .project(project)
                .skill(skill)
                .weight(weight)
                .build();
    }

    public void increaseWeight(double weight) {
        this.weight += weight;
    }

    public void decreaseWeight(double amount) {
        this.weight -= amount;
    }

    public boolean isWeightZeroOrNegative() {
        return this.weight <= 0;
    }
}
