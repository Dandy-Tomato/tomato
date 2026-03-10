package site.to_mato.topic.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.common.entity.BaseEntity;
import site.to_mato.project.entity.Project;
import site.to_mato.topic.entity.enums.Reaction;

@Getter
@Entity
@Table(
        name = "project_topic_reactions",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_project_topic_reaction",
                        columnNames = {"project_id", "topic_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProjectTopicReaction extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_topic_reaction_id")
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Reaction reaction;

    @Version
    @Column(nullable = false)
    private Long version;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private Topic topic;

    @Builder
    private ProjectTopicReaction(Project project, Topic topic, Reaction reaction) {
        this.project = project;
        this.topic = topic;
        this.reaction = reaction;
    }

    public static ProjectTopicReaction of(Project project, Topic topic, Reaction reaction) {
        return ProjectTopicReaction.builder()
                .project(project)
                .topic(topic)
                .reaction(reaction)
                .build();
    }


    public void changeReaction(Reaction reaction) {
        this.reaction = reaction;
    }

}
