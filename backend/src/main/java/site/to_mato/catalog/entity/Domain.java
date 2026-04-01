package site.to_mato.catalog.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table(name = "domains")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Domain {

    @Id
    @Column(name = "domain_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false, unique = true)
    private String name;
}
