package site.to_mato.topic.entity;

import jakarta.persistence.*;
import lombok.Getter;

@Getter
@Entity
@Table(name = "topics")
public class Topic {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "topic_id")
    private Long id;

    @Column(name = "title")
    private String title;

    @Column(name = "description")
    private String description;

    @Column(name = "expected_duration_week")
    private int expectedDurationWeek;

    @Column(name = "recommended_team_size")
    private int recommendedTeamSize;

    @Column(name = "difficulty")
    private int difficulty;

    @Column(name = "tech_stacks")
    private String techStacks;

    @Column(name = "domain_id")
    private Long domainId;

    @Column(name = "source_repo_id")
    private Long sourceRepoId;

}
