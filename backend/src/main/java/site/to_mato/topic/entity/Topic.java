package site.to_mato.topic.entity;

import lombok.AccessLevel;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Domain;

@Getter
@Entity
@Table(name = "topics")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Topic {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "topic_id")
    private Long id;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "expected_duration_week", nullable = false)
    private int expectedDurationWeek;

    @Column(name = "recommended_team_size", nullable = false)
    private int recommendedTeamSize;

    @Column(name = "difficulty")
    private Integer difficulty;

    @Column(name = "topic_embedding", columnDefinition = "vector(1536)")
    @JdbcTypeCode(SqlTypes.VECTOR)
    private float[] topicEmbedding;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "domain_id", nullable = false)
    private Domain domain;

    @Column(name = "source_repo_id", nullable = false)
    private Long sourceRepoId;
}
