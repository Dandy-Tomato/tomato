package site.to_mato.project.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Domain;

@Getter
@Entity
@Table(name = "project_domains")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProjectDomain {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_domain_id")
    private Long id;

    @Column(name = "weight")
    private Double weight;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "domain_id", nullable = false)
    private Domain domain;

    @Builder
    private ProjectDomain(
            Double weight,
            Project project,
            Domain domain
    ) {
        validateWeight(weight);
        this.weight = weight;
        this.project = project;
        this.domain = domain;
    }

    public static ProjectDomain of(
            Project project,
            Domain domain,
            Double weight
    ) {
        return ProjectDomain.builder()
                .project(project)
                .domain(domain)
                .weight(weight)
                .build();
    }

    public void updateWeight(Double weight) {
        validateWeight(weight);
        this.weight = weight;
    }

    private void validateWeight(Double weight) {
        if (weight == null || weight < 0) {
            throw new IllegalArgumentException("weight는 null일 수 없고 0 이상이어야 합니다.");
        }
    }
}
