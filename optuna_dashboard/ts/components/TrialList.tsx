import React, { FC, useState } from "react"
import {
  Typography,
  Box,
  Card,
  CardContent,
  useTheme,
  CardHeader,
  Grid,
} from "@mui/material"
import Chip from "@mui/material/Chip"
import Divider from "@mui/material/Divider"
import List from "@mui/material/List"
import ListItem from "@mui/material/ListItem"
import ListItemButton from "@mui/material/ListItemButton"
import ListItemText from "@mui/material/ListItemText"
import ListSubheader from "@mui/material/ListSubheader"

import { TrialNote } from "./Note"
import { DataGrid, DataGridColumn } from "./DataGrid"
import { Link } from "react-router-dom"

export const TrialList: FC<{
  studyDetail: StudyDetail | null
  trialNumber: number | null
}> = ({ studyDetail, trialNumber }) => {
  const theme = useTheme()
  const [selected, setSelected] = useState<number>(trialNumber || 0)
  const trials: Trial[] = studyDetail !== null ? studyDetail.trials : []
  const trialListWidth = 240

  const isBestTrial = (trialId: number) => {
    const bestTrialIDs = studyDetail?.best_trials.map((t) => t.trial_id) || []
    return bestTrialIDs.findIndex((a) => a === trialId) != -1
  }

  const collapseIntermediateValueColumns: DataGridColumn<TrialIntermediateValue>[] =
    [
      { field: "step", label: "Step", sortable: true },
      {
        field: "value",
        label: "Value",
        sortable: true,
        less: (firstEl, secondEl): number => {
          const firstVal = firstEl.value
          const secondVal = secondEl.value
          if (firstVal === secondVal) {
            return 0
          }
          if (firstVal === "nan") {
            return -1
          } else if (secondVal === "nan") {
            return 1
          }
          if (firstVal === "-inf" || secondVal === "inf") {
            return 1
          } else if (secondVal === "-inf" || firstVal === "inf") {
            return -1
          }
          return firstVal < secondVal ? 1 : -1
        },
      },
    ]
  const collapseAttrColumns: DataGridColumn<Attribute>[] = [
    { field: "key", label: "Key", sortable: true },
    { field: "value", label: "Value", sortable: true },
  ]

  let content = null
  if (trials.length > selected) {
    const trial = trials[selected]
    content = (
      <>
        <Card sx={{ margin: theme.spacing(2) }}>
          <CardHeader
            title={`Trial ${trial.number} (trial_id=${trial.trial_id})`}
          />
          <CardContent>
            {isBestTrial(trial.trial_id) ? (
              <Chip
                label={"Best Trial"}
                color="primary"
                sx={{ marginBottom: theme.spacing(1) }}
                size="small"
              />
            ) : null}
            <Typography>
              Values:{" "}
              {trial.values?.map((v) => v.toString()).join(" ") || "None"}
            </Typography>
            <Typography>
              Params = [
              {trial.params.map((p) => `${p.name}: ${p.value}`).join(", ")}]
            </Typography>
          </CardContent>
        </Card>
        <TrialNote
          studyId={trial.study_id}
          trialId={trial.trial_id}
          latestNote={trial.note}
        />
        <Grid
          container
          direction="row"
          spacing={2}
          sx={{ p: theme.spacing(0, 2) }}
        >
          <Grid item xs={6}>
            <Card>
              <CardHeader title="Intermediate Values" />
              <CardContent>
                <DataGrid<TrialIntermediateValue>
                  columns={collapseIntermediateValueColumns}
                  rows={trial.intermediate_values}
                  keyField={"step"}
                  dense={true}
                  rowsPerPageOption={[5, 10, { label: "All", value: -1 }]}
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardHeader title="User Attributes" />
              <CardContent>
                <DataGrid<Attribute>
                  columns={collapseAttrColumns}
                  rows={trial.user_attrs}
                  keyField={"key"}
                  dense={true}
                  rowsPerPageOption={[5, 10, { label: "All", value: -1 }]}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </>
    )
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "row", width: "100%" }}>
      <Box
        sx={{
          width: trialListWidth,
          overflow: "auto",
          height: `calc(100vh - ${theme.spacing(8)})`,
        }}
      >
        <List>
          <ListSubheader>{`${
            studyDetail?.trials.length || 0
          } Trials`}</ListSubheader>
          {trials.map((trial, i) => {
            let color:
              | "default"
              | "primary"
              | "secondary"
              | "error"
              | "info"
              | "success"
              | "warning" = "default"
            if (trial.state === "Complete") {
              color = "success"
            } else if (trial.state === "Running") {
              color = "secondary"
            } else if (trial.state === "Waiting") {
              color = "secondary"
            } else if (trial.state === "Pruned") {
              color = "warning"
            } else if (trial.state === "Fail") {
              color = "error"
            }
            return (
              <ListItem key={trial.trial_id} disablePadding>
                <ListItemButton
                  component={Link}
                  to={
                    URL_PREFIX +
                    `/studies/${trial.study_id}/trials/${trial.number}`
                  }
                  onClick={() => {
                    setSelected(trial.number)
                  }}
                  selected={i === selected}
                >
                  <ListItemText
                    primary={`Trial ${trial.number}`}
                    secondary={
                      <Box sx={{ padding: theme.spacing(1, 0) }}>
                        <Chip color={color} label={trial.state} size="small" />
                        {isBestTrial(trial.trial_id) ? (
                          <Chip
                            label={"Best Trial"}
                            color="primary"
                            sx={{ marginLeft: theme.spacing(1) }}
                            size="small"
                          />
                        ) : null}
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            )
          })}
        </List>
      </Box>
      <Divider orientation="vertical" flexItem />
      <Box
        sx={{
          flexGrow: 1,
          overflow: "auto",
          height: `calc(100vh - ${theme.spacing(8)})`,
        }}
      >
        {content}
      </Box>
    </Box>
  )
}