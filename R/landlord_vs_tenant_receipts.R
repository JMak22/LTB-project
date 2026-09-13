landlord_vs_tenant_receipts <- function() {
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)

  df <- read_csv(here::here("cleaned_data", "landlord_vs_tenant_receipts.csv"))

  glimpse(df)

  df |>
    pivot_longer(
      c(landlord_received, tenant_received),
      names_to = "recipient",
      values_to = "received_amount"
    ) |>
    mutate(recipient = stringr::str_replace_all(recipient, "_received", "")) |>
    ggplot() +
    aes(x = received_amount, y = report_id, fill = recipient) +
    geom_col() +
    labs(
      title = "Landord vs Tenant receipts",
      subtitle = "1998-2024",
      caption = "Source: <add source>"
    ) +
    scale_fill_manual(values = c("landlord" = "#df0000", tenant = "#006fff")) +
    scale_x_continuous(
      labels = scales::label_percent(),
      breaks = seq(0, 1, .1)
    ) +
    theme_minimal()
}
