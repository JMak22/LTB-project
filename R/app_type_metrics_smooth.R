app_type_metrics <- readr::read_csv("cleaned_data/app_type_metrics.csv")

library(ggplot2)
app_type_metrics |> 
  dplyr::filter(
    app_code == "L5",
  metric_id == "cases") |>
  dplyr::mutate(
    value = as.numeric(value),
    year = as.numeric(substr(report_id, 1, 4)
  )
  ) |> 
ggplot()+
  aes(x = year, y = value)+
  geom_point()+
  geom_smooth(method = "loess", se = TRUE)


# make it interactive with ggiraph
library(ggiraph)
app_type_metrics |>
  dplyr::filter(
    app_code == "L5",
    metric_id == "cases") |>
  dplyr::mutate(
    value = as.numeric(value),
    year = as.numeric(substr(report_id, 1, 4)
  )
  ) -> df
  
library(zoo) # for rollmean
p <- ggplot(df)+
  aes(x = year, y = value)+
  geom_point_interactive(aes(tooltip = value))+
  geom_smooth(method = "loess", se = FALSE)+
  geom_smooth(method = "lm", se = FALSE, color = "red3")+
  # add a curve that shows the 5 year moving average
  geom_smooth(aes(y = rollmean(value, k = 1, align = "right", fill = NA)), method = "loess", se = FALSE, color = "#ffefef", linetype = "dashed", linewidth = .5)+
  geom_smooth(aes(y = rollmean(value, k = 2, align = "right", fill = NA)), method = "loess", se = FALSE, color = "#ffcecf", linetype = "dashed", linewidth = .5)+
  geom_smooth(aes(y = rollmean(value, k = 3, align = "right", fill = NA)), method = "loess", se = FALSE, color = "#ff9dbf", linetype = "dashed", linewidth = .5)+
  geom_smooth(aes(y = rollmean(value, k = 4, align = "right", fill = NA)), method = "loess", se = FALSE, color = "#ff6ca0", linetype = "dashed", linewidth = .5)+
  geom_smooth(aes(y = rollmean(value, k = 5, align = "right", fill = NA)), method = "loess", se = FALSE, color = "#ff3b82", linetype = "dashed", linewidth = .5)+
  geom_line(aes(y = rollmean(value, k = 1, align = "right", fill = NA)), color = "#efefff", linetype = "dashed")+
  geom_line(aes(y = rollmean(value, k = 2, align = "right", fill = NA)), color = "#cecfff", linetype = "dashed")+
  geom_line(aes(y = rollmean(value, k = 3, align = "right", fill = NA)), color = "#9dbfff", linetype = "dashed")+
  geom_line(aes(y = rollmean(value, k = 4, align = "right", fill = NA)), color = "#6ca0ff", linetype = "dashed")+
  geom_line(aes(y = rollmean(value, k = 5, align = "right", fill = NA)), color = "#3b82f6", linetype = "dashed")+
  theme_minimal()+
  labs(
    title = "Cases over time for L5",
    x = "Year",
    y = "Number of Cases"
  ) 
p




# we'll just do a bar chart
library(ggplot2)
app_type_metrics |> 
  dplyr::filter(
    app_code == "L5",
  metric_id == "cases") |>
  dplyr::mutate(
    value = as.numeric(value),
    year = as.numeric(substr(report_id, 1, 4)
  )
  ) |>dplyr::select(year, value) -> df  
  # print without line numbers
  p
  # print(n = Inf) 
ggplot(df)+
  aes(x = year, y = value)+
  geom_col()


library(segmented)

m0 <- lm(value ~ year, data = df)
m1 <- segmented(m0, seg.Z = ~year)

summary(m1)

bp <- m1$psi[2]
bp

library(ggplot2)

df$pred_seg <- predict(m1)

ggplot(df, aes(year, value)) +
  geom_point() +
  # geom_line(alpha = 0.3) +
  
  # segmented regression line
  geom_line(aes(y = pred_seg), color = "darkred", linewidth = .5) +
  
  # LOESS for gentle trend context
  # geom_smooth(method = "loess", span = 0.8, se = FALSE, color = "steelblue", linewidth = 0.5) +
  
  # 5-year centered moving average
  geom_line(aes(y = rollmean(value, 5, align = "center", fill = NA)),color = "darkgreen", linewidth = 0.5) +
  
  theme_minimal() +
  labs(
    title = "Cases over time for L5",
    subtitle = "Segmented regression, LOESS (span=0.8), and 5-year centered moving average",
    x = "Year",
    y = "Number of Cases"
  )
