"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

interface GlobeProps {
  className?: string;
}

export default function Globe({ className }: GlobeProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 3.5);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const nvidiaGreen = new THREE.Color("#76B900");
    const nvidiaGlow = new THREE.Color(rgba(118, 185, 0, 0.3));
    const darkGreen = new THREE.Color("#3a5c00");

    const sphereRadius = 1.4;
    const segments = 32;

    const geo = new THREE.IcosahedronGeometry(sphereRadius, 4);
    const edges = new THREE.EdgesGeometry(geo);
    const wireframe = new THREE.LineSegments(
      edges,
      new THREE.LineBasicMaterial({
        color: nvidiaGreen,
        transparent: true,
        opacity: 0.4,
      })
    );
    scene.add(wireframe);

    const innerSphere = new THREE.Mesh(
      new THREE.SphereGeometry(sphereRadius * 0.98, segments, segments),
      new THREE.MeshBasicMaterial({
        color: "#0a0a0a",
        transparent: true,
        opacity: 0.15,
        wireframe: true,
      })
    );
    scene.add(innerSphere);

    const particleCount = 800;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = sphereRadius + 0.3 + Math.random() * 0.8;
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.cos(phi);
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
      sizes[i] = 0.01 + Math.random() * 0.03;
    }

    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    const particleMat = new THREE.PointsMaterial({
      color: nvidiaGreen,
      size: 0.02,
      transparent: true,
      opacity: 0.6,
      sizeAttenuation: true,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    const connectionPoints: THREE.Vector3[] = [];
    for (let i = 0; i < 40; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = sphereRadius * 1.01;
      connectionPoints.push(
        new THREE.Vector3(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.cos(phi),
          r * Math.sin(phi) * Math.sin(theta)
        )
      );
    }

    const lineMat = new THREE.LineBasicMaterial({
      color: nvidiaGreen,
      transparent: true,
      opacity: 0.08,
    });

    for (let i = 0; i < connectionPoints.length; i++) {
      for (let j = i + 1; j < connectionPoints.length; j++) {
        if (Math.random() < 0.15) {
          const points = [connectionPoints[i], connectionPoints[j]];
          const g = new THREE.BufferGeometry().setFromPoints(points);
          const line = new THREE.Line(g, lineMat);
          scene.add(line);
        }
      }
    }

    const glowGeo = new THREE.SphereGeometry(sphereRadius * 1.6, 32, 32);
    const glowMat = new THREE.MeshBasicMaterial({
      color: nvidiaGreen,
      transparent: true,
      opacity: 0.03,
    });
    const glowMesh = new THREE.Mesh(glowGeo, glowMat);
    scene.add(glowMesh);

    let time = 0;

    function animate() {
      requestAnimationFrame(animate);
      time += 0.003;

      wireframe.rotation.y = time * 0.3;
      wireframe.rotation.x = Math.sin(time * 0.1) * 0.05;
      innerSphere.rotation.y = time * 0.3;
      innerSphere.rotation.x = Math.sin(time * 0.1) * 0.05;
      particles.rotation.y = time * 0.25;
      particles.rotation.x = Math.sin(time * 0.08) * 0.03;
      glowMesh.rotation.y = time * 0.2;

      const pulse = 0.03 + Math.sin(time * 0.5) * 0.015;
      glowMat.opacity = pulse;
      const scale = 1 + Math.sin(time * 0.5) * 0.02;
      glowMesh.scale.set(scale, scale, scale);

      renderer.render(scene, camera);
    }

    animate();

    function handleResize() {
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: "100%", height: "100%", minHeight: "400px" }}
    />
  );
}

function rgba(r: number, g: number, b: number, a: number): string {
  return `rgba(${r},${g},${b},${a})`;
}
