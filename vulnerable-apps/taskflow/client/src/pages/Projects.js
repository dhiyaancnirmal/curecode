import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import api from '../services/api';

const Projects = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newProject, setNewProject] = useState({ name: '', description: '' });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (err) {
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/projects', newProject);
      setProjects([...projects, response.data]);
      setNewProject({ name: '', description: '' });
    } catch (err) {
      console.error('Error creating project:', err);
    }
  };

  const handleDeleteProject = async (projectId) => {
    try {
      await api.delete(`/projects/${projectId}`);
      setProjects(projects.filter(project => project.id !== projectId));
    } catch (err) {
      console.error('Error deleting project:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading projects...</div>;
  }

  return (
    <div className="projects-page">
      <h1>My Projects</h1>
      
      <div className="create-project-form">
        <h3>Create New Project</h3>
        <form onSubmit={handleCreateProject}>
          <input
            type="text"
            placeholder="Project name"
            value={newProject.name}
            onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
            required
          />
          <textarea
            placeholder="Project description"
            value={newProject.description}
            onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
          />
          <button type="submit" className="btn btn-primary">Create Project</button>
        </form>
      </div>
      
      <div className="projects-list">
        <h3>All Projects</h3>
        {projects.length > 0 ? (
          <div className="project-grid">
            {projects.map(project => (
              <div key={project.id} className="project-card">
                <h4>{project.name}</h4>
                <p>{project.description}</p>
                <div className="project-meta">
                  <span className="project-tasks">{project.taskCount || 0} tasks</span>
                  <span className="project-date">{new Date(project.createdAt).toLocaleDateString()}</span>
                </div>
                <button 
                  onClick={() => handleDeleteProject(project.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p>No projects found</p>
        )}
      </div>
    </div>
  );
};

export default Projects;
