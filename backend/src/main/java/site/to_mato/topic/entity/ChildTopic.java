package site.to_mato.topic.entity;

import jakarta.persistence.Column;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.project.entity.Project;
import site.to_mato.common.entity.BaseEntity;

@Getter
@Entity
@Table(name = "child_topics")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ChildTopic extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "child_topic_id")
    private Long id;

    @Column(name = "title")
    private String title;

    @Column(name = "content", columnDefinition = "text")
    private String content;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private Topic topic;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    private Project project;

    @Builder(access = AccessLevel.PRIVATE)
    private ChildTopic(String title, String content, Topic topic, Project project) {
        this.title = title;
        this.content = content;
        this.topic = topic;
        this.project = project;
    }

    public static ChildTopic create(String title, String content, Topic topic, Project project) {
        return ChildTopic.builder()
                .title(title)
                .content(content)
                .topic(topic)
                .project(project)
                .build();
    }
}
