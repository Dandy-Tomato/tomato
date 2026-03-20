package site.to_mato.topic.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.common.entity.BaseEntity;

@Getter
@Entity
@Table(
        name = "project_topic_bookmarks",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_project_topic_bookmark",
                        columnNames = {"project_id", "topic_id"}
                )
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProjectTopicBookmark extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "project_topic_bookmark_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private Topic topic;

    @Builder
    private ProjectTopicBookmark(Project project, Topic topic) {
        this.project = project;
        this.topic = topic;
    }

    public static ProjectTopicBookmark of(Project project, Topic topic) {
        return ProjectTopicBookmark.builder()
                .project(project)
                .topic(topic)
                .build();
    }
}
