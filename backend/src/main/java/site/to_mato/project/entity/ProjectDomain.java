package site.to_mato.project.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Domain;

@Getter
@Entity
@Table(
        name = "project_domains",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_project_domain",
                        columnNames = {"project_id", "domain_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProjectDomain {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_domain_id")
    private Long id;

    @Column(name = "weight")
    private double weight;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "domain_id", nullable = false)
    private Domain domain;

    @Builder(access = AccessLevel.PRIVATE)
    private ProjectDomain(
            Project project,
            Domain domain,
            double weight
    ) {
        this.project = project;
        this.domain = domain;
        this.weight = weight;
    }

    public static ProjectDomain of(Project project, Domain domain, double weight) {
        return ProjectDomain.builder()
                .project(project)
                .domain(domain)
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
