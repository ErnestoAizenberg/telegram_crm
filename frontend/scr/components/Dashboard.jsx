import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Message,
  People,
  TrendingUp,
  ChatBubble
} from '@mui/icons-material';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState({});
  const [recentConversations, setRecentConversations] = useState([]);

  useEffect(() => {
    fetchAnalytics();
    fetchRecentConversations();
  }, []);

  const fetchAnalytics = async () => {
    const response = await fetch('/api/analytics/');
    const data = await response.json();
    setAnalytics(data);
  };

  const fetchRecentConversations = async () => {
    const response = await fetch('/api/conversations/?limit=5');
    const data = await response.json();
    setRecentConversations(data.results || []);
  };

  const StatCard = ({ icon, title, value, subtitle }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          {icon}
          <Typography variant="h6" component="div" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div">
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        CRM Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<Message color="primary" />}
            title="Messages Sent"
            value={analytics.messages_sent || 0}
            subtitle="This month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<ChatBubble color="secondary" />}
            title="Messages Received"
            value={analytics.messages_received || 0}
            subtitle="This month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<People color="success" />}
            title="New Contacts"
            value={analytics.new_contacts || 0}
            subtitle="This month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<TrendingUp color="warning" />}
            title="Response Rate"
            value={`${analytics.response_rate?.toFixed(1) || 0}%`}
            subtitle="Efficiency"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Conversations
            </Typography>
            <List>
              {recentConversations.map((conversation, index) => (
                <React.Fragment key={conversation.id}>
                  <ListItem>
                    <ListItemText
                      primary={conversation.contact.first_name || conversation.contact.username}
                      secondary={`Last message: ${new Date(conversation.last_message_at).toLocaleString()}`}
                    />
                  </ListItem>
                  {index < recentConversations.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            {/* Add quick action buttons here */}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;