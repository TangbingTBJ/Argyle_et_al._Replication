library(psych)   
library(caret)
library(ggplot2)
library(reshape2)
library(xtable)
library(tidyverse)
knitr::opts_chunk$set(echo = TRUE)
setwd(dirname(rstudioapi::getSourceEditorContext()$path))

#load all files and update file name
formal_names <- c("short_attend_church_2012", "short_discuss_politics_2012", 
               "short_political_interest_2012", "short_attend_church_2016", 
               "short_discuss_politics_2016", "short_political_interest_2016", 
               "short_attend_church_2020", "short_discuss_politics_2020", 
               "short_political_interest_2020")


csv_short <- list.files(path = ".", pattern = "^short.*\\.csv$", full.names = TRUE)
for (i in seq_along(csv_short)) {
  df <- read.csv(csv_short[i])
  df <- df[, !grepl("completion$", names(df))]
  assign(formal_names[i], df, envir = .GlobalEnv)
}

for (df_name in formal_names) {
  df <- get(df_name)
  predictions <- tail(names(df), 2)
  df[predictions] <- lapply(df[predictions], function(col) as.numeric(as.character(col)))
  df <- df[complete.cases(df[predictions]), ]
  if (grepl("short_attend_church|short_discuss_politics", df_name)) {
    df <- df[df[[predictions[1]]] %in% c(1, 2) & df[[predictions[2]]] %in% c(1, 2), ]
  } else if (grepl("short_political_interest", df_name)) {
    df <- df[df[[predictions[1]]] %in% 1:4 & df[[predictions[2]]] %in% 1:4, ]
  }
  
  assign(df_name, df, envir = .GlobalEnv)
}

metrics_short <- data.frame(
  target_var = character(),
  year = numeric(),
  model = character(),
  proportion = numeric(),
  kappa = numeric(),
  f1 = numeric(),
  ICC = numeric(),
  tetrachoric = numeric(),
  optimized = character()
)

for (df_name in formal_names) {
  models <- c("gpt.3.5.turbo", "gpt.4o.mini")
  df <- get(df_name)
  target_var <- names(df)[2]
  
  for (model in models) {
    df[[target_var]] <- as.factor(df[[target_var]])
    df[[model]] <- as.factor(df[[model]])
    
    cont_table <- table(df[[target_var]], df[[model]])
    proportion <- round(sum(diag(prop.table(cont_table))), 2)
    
    kappa <- round(cohen.kappa(cbind(df[[target_var]], df[[model]]))$kappa, 2)
    
    # Compute confusion matrix and F1 score
    conf_matrix <- confusionMatrix(df[[model]], df[[target_var]])
    per_class_metrics <- conf_matrix$byClass
    
    if (names(df)[2] != "political_interest") {
      f1 <- round(per_class_metrics["F1"], 2)
    } else {
      class_counts <- table(df[[target_var]])
      f1 <- tryCatch({
        # Fix row name mismatch ("Class: 1" vs "1")
        row_classes <- gsub("Class: ", "", rownames(per_class_metrics))
        common_classes <- intersect(row_classes, names(class_counts))
        
        f1_scores <- per_class_metrics[match(paste0("Class: ", common_classes), rownames(per_class_metrics)), "F1"]
        class_counts_used <- class_counts[common_classes]
        
        # Remove names to avoid misaligned multiplication
        names(f1_scores) <- NULL
        names(class_counts_used) <- NULL
        
        valid <- !is.na(f1_scores)
        round(sum(f1_scores[valid] * class_counts_used[valid]) / sum(class_counts_used[valid]), 2)
      }, error = function(e) {
        print(paste("F1 error at:", df_name, "Model:", model, "Error:", e$message))
        NA
      })
    }
    # Compute ICC using dynamic columns
    ICC <- round(min(ICC(cbind(df[[target_var]], df[[model]]))$results$ICC[4:6]), 2)
    
    # Compute tetrachoric correlation
    if (names(df)[2] != "political_interest") {
      tetrachoric <- round(tetrachoric(cbind(df[[target_var]], df[[model]]))$rho[2], digits = 2)
    } else {
      tetrachoric <- NA
    }
    
    # Append metrics to the data frame
    metrics_short <- rbind(metrics_short, data.frame(
      target_var = target_var,
      year = as.numeric(sub(".*_(\\d{4})$", "\\1", df_name)),
      model = model,
      proportion = proportion,
      kappa = kappa,
      f1 = f1,
      ICC = ICC,
      tetrachoric = tetrachoric,
      optimized = 'yes'
      ))
  }
}

#import metrics from study 3 for comparison
metrics_study_3 <- read_csv('metric_scores_no_na.csv')
metrics_study_3 <- metrics_study_3[, c("target_var", "year", 'model','proportion',
                                       'kappa','f1','ICC','tetrachoric')]
metrics_study_3 <- metrics_study_3 %>% mutate(model = recode(model, 
                                             'gpt_3_5_turbo' = 'gpt.3.5.turbo', 
                                             'gpt_4o_mini'='gpt.4o.mini',
                                             'gpt_4' = 'gpt.4'),
                                             target_var = recode(target_var,
                                                                 'church_goer' = 'attend_church'),
                                             optimized = 'no') %>%
  filter(model != 'gpt_3')

metrics <- rbind(metrics_study_3,metrics_short)

subset_for_graphing <- function(target_var_input, year_input) {
  if (target_var_input == 'political_interest') {
    df_temp <- metrics %>%
      filter(target_var == target_var_input, year == year_input) %>%
      select(model, proportion, f1, kappa, ICC,optimized) %>%
      mutate(across(where(is.numeric), ~ replace(., is.na(.), NA))) %>%
      pivot_longer(cols = c(proportion, f1, kappa, ICC),
                   names_to = "metric",
                   values_to = "value")
  } else {
    df_temp <- metrics %>%
      filter(target_var == target_var_input, year == year_input) %>%
      select(model, proportion, f1, kappa, ICC, tetrachoric,optimized) %>%
      mutate(across(where(is.numeric), ~ replace(., is.na(.), NA))) %>%
      pivot_longer(cols = c(proportion, f1, kappa,ICC,tetrachoric),
                   names_to = "metric",
                   values_to = "value")
  }
  if(year_input != 2016){
    df_temp$model <- factor(df_temp$model, levels = c("gpt.3.5.turbo",'gpt.3.5.turbo.optimized', "gpt.4o.mini",'gpt.4o.mini.optimized', "gpt.4"))
  }
  df_temp$model <- factor(df_temp$model, levels = c("gpt.3.5.turbo",'gpt.3.5.turbo.optimized', "gpt.4o.mini",'gpt.4o.mini.optimized','gpt.3', "gpt.4"))
  if(target_var_input == 'political_interest'){
    df_temp$metric <- factor(df_temp$metric, levels = c("proportion", "f1", "kappa", "ICC"))
  }
  df_temp$metric <- factor(df_temp$metric, levels = c("proportion", "f1", "kappa", "ICC",'tetrachoric'))
  df_temp$optimized <- factor(df_temp$optimized, levels = c("yes",'no'))
  return(df_temp)
}

political_interest_2012 <- subset_for_graphing('political_interest',2012)
political_interest_2016 <- subset_for_graphing('political_interest',2016)
political_interest_2020 <- subset_for_graphing('political_interest',2020)


# Plot
annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(political_interest_2012$model)),
  x = 2.4,
  y = 0.65,
  label = "Year: 2012"
)
legend_labels <- data.frame(
  model = factor("gpt.4", levels = levels(political_interest_2012$model)),
  x_tile = c(1.7, 1.7),          
  x_text = c(1.8, 1.8),          
  y = c(0.60, 0.54),             
  label = c("Optimized", "Non-Optimized"),
  fill = c("yes", "no")
)

pi_12 <- ggplot(political_interest_2012, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(political_interest_2012, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(political_interest_2012, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.7),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  geom_tile(
    data = legend_labels,
    aes(x = x_tile, y = y, fill = fill),
    width = 0.15,
    height = 0.025,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = legend_labels,
    aes(x = x_text, y = y, label = label),
    size = 6,
    hjust = 0,  # left-align text
    inherit.aes = FALSE
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_text(size = 20),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.68),breaks = seq(0,0.65,by=0.15))

pi_12
ggsave("./figures/political_interest_2012.png", plot = pi_12, width = 13.7, height = 6.8, units = "in", dpi = 300)

#2016

annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(political_interest_2012$model)),
  x = 2.4,
  y = 0.53,
  label = "Year: 2016"
)
pi_16 <- ggplot(political_interest_2016, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(political_interest_2016, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(political_interest_2016, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.55),breaks = seq(0,0.55,by=0.1))

pi_16
ggsave("./figures/political_interest_2016.png", plot = pi_16, width = 13.7, height = 6.8, units = "in", dpi = 300)


annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(political_interest_2020$model)),
  x = 2.4,
  y = 0.48,
  label = "Year: 2020"
)
pi_20 <- ggplot(political_interest_2020, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(political_interest_2020, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(political_interest_2020, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20,angle = 45, hjust = 1),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.5),breaks = seq(0,0.5,by=0.1))

pi_20
ggsave("./figures/political_interest_2020.png", plot = pi_20, width = 13.7, height = 6.8, units = "in", dpi = 300)
###########################political discussion#####################
discuss_politics_2012 <- subset_for_graphing('discuss_politics',2012)
discuss_politics_2016 <- subset_for_graphing('discuss_politics',2016)
discuss_politics_2020 <- subset_for_graphing('discuss_politics',2020)




# Plot
annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(discuss_politics_2012$model)),
  x = 3.5,
  y = 0.83,
  label = "Year: 2012"
)
legend_labels <- data.frame(
  model = factor("gpt.4", levels = levels(discuss_politics_2012$model)),
  x_tile = c(2.8, 2.8),            # align under annotation at x = 4
  x_text = c(3.1, 3.1),            # text to the right of tiles
  y = c(0.77, 0.72),               # just below annotation y = 0.83
  label = c("Optimized", "Non-Optimized"),
  fill = c("yes", "no")
)

dp_12 <- ggplot(discuss_politics_2012, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(discuss_politics_2012, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(discuss_politics_2012, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.7),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  geom_tile(
    data = legend_labels,
    aes(x = x_tile, y = y, fill = fill),
    width = 0.15,
    height = 0.025,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = legend_labels,
    aes(x = x_text, y = y, label = label),
    size = 7,
    hjust = 0,  # left-align text
    inherit.aes = FALSE
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_text(size = 20),
    panel.spacing.x = unit(0.8, "lines")
  ) 

dp_12
ggsave("./figures/political_discussion_2012.png", plot = dp_12, width = 13.7, height = 6.8, units = "in", dpi = 300)

#2016
annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(discuss_politics_2016$model)),
  x = 3.7,
  y = 0.9,
  label = "Year: 2016"
)
dp_16 <- ggplot(discuss_politics_2016, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(discuss_politics_2016, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(discuss_politics_2016, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(-0.39, 0.95),breaks = seq(-0.35,0.95,by=0.2))

dp_16
ggsave("./figures/political_discussion_2016.png", plot = dp_16, width = 13.7, height = 6.8, units = "in", dpi = 300)



annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(discuss_politics_2020$model)),
  x = 3.7,
  y = 0.9,
  label = "Year: 2020"
)
dp_20 <- ggplot(discuss_politics_2020, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(discuss_politics_2020, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(discuss_politics_2020, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20,angle = 45, hjust = 1),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(-0.3, 0.99),breaks = seq(-0.3,0.97,by=0.2))

dp_20
ggsave("./figures/political_discussion_2020.png", plot = dp_20, width = 13.7, height = 6.8, units = "in", dpi = 300)

###########################attend church#####################
attend_church_2012 <- subset_for_graphing('attend_church',2012)
attend_church_2016 <- subset_for_graphing('attend_church',2016)
attend_church_2020 <- subset_for_graphing('attend_church',2020)

annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(attend_church_2012$model)),
  x = 3.5,
  y = 0.83,
  label = "Year: 2012"
)
legend_labels <- data.frame(
  model = factor("gpt.4", levels = levels(attend_church_2012$model)),
  x_tile = c(2.8, 2.8),            # align under annotation at x = 4
  x_text = c(3.1, 3.1),            # text to the right of tiles
  y = c(0.77, 0.72),               # just below annotation y = 0.83
  label = c("Optimized", "Non-Optimized"),
  fill = c("yes", "no")
)

ac_12 <- ggplot(attend_church_2012, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(attend_church_2012, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(attend_church_2012, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.7),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  geom_tile(
    data = legend_labels,
    aes(x = x_tile, y = y, fill = fill),
    width = 0.15,
    height = 0.025,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = legend_labels,
    aes(x = x_text, y = y, label = label),
    size = 7,
    hjust = 0,  # left-align text
    inherit.aes = FALSE
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_text(size = 20),
    panel.spacing.x = unit(0.8, "lines")
  ) 

ac_12
ggsave("./figures/attend_church_2012.png", plot = ac_12, width = 13.7, height = 6.8, units = "in", dpi = 300)


#2016
annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(attend_church_2016$model)),
  x = 3.7,
  y = 0.75,
  label = "Year: 2016"
)
ac_16 <- ggplot(attend_church_2016, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(attend_church_2016, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(attend_church_2016, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.77),breaks = seq(0,0.8,by=0.15))

ac_16
ggsave("./figures/attend_church_2016.png", plot = ac_16, width = 13.7, height = 6.8, units = "in", dpi = 300)

#2020
annotation_df <- data.frame(
  model = factor("gpt.4", levels = levels(attend_church_2020$model)),
  x = 3.7,
  y = 0.7,
  label = "Year: 2020"
)
ac_20 <- ggplot(attend_church_2020, aes(x = metric, y = value, fill = optimized)) +
  geom_bar(
    data = filter(attend_church_2020, model != "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_bar(
    data = filter(attend_church_2020, model == "gpt.4"),
    aes(x = metric, y = value, fill = optimized),
    stat = "identity",
    position = position_dodge(width = 0.9),
    width = 0.4
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("no" = "#F8766D", "yes" = "#00BFC4")) +
  labs(title = "",
       x = "", y = "", fill = "Optimized") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20,angle = 45, hjust = 1),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.7),breaks = seq(0.15,0.97,by=0.15))

ac_20
ggsave("./figures/attend_church_2020.png", plot = ac_20, width = 13.7, height = 6.8, units = "in", dpi = 300)





political_interest_2016_confusion <- short_political_interest_2016 %>% filter(model == 'gpt.4o.mini')
political_interest_2016_confusion$political_interest <- factor(political_interest_2016_confusion$political_interest, levels=c(1,2,3,4))
political_interest_2016_confusion$gpt.4o.mini <- factor(political_interest_2016_confusion$gpt.4o.mini, levels=c(1,2,3,4))

political_interest_2016_conf_matrix <- confusionMatrix(political_interest_2016_confusion$gpt.4o.mini, political_interest_2016_confusion$political_interest)

political_interest_conf_table <- as.data.frame(political_interest_2016_conf_matrix$table)
colnames(political_interest_conf_table) <- c("GPT", "ANES", "Count")

political_interest_conf_table <- political_interest_conf_table %>%
  mutate(
    Percentage = round((Count /  sum(political_interest_conf_table$Count)) * 100, 2),
    Label = paste0(Count, "\n(", Percentage, "%)")
  )
heatmap_political_interest <- ggplot(political_interest_conf_table, aes(x = ANES, y = GPT, fill = Count)) +
  geom_tile(color = "gray", linewidth = 0.5) +
  geom_text(aes(label = Label), color = "black", size = 7, fontface = "bold") +
  scale_fill_gradient(low = "white", high = "#1f77b4", name = "Count") +
  theme_minimal(base_size = 14) +
  labs(
    title = "",
    x = "ANES",
    y = "GPT") +
  theme(
    legend.position = "none", 
    axis.title = element_text(size = 20),
    axis.text = element_text(size = 20),
    plot.caption = element_text(size = 20, hjust = 0),
  ) +
  scale_x_discrete(labels = c("Very", "Somewhat", "Slightly", "Not at all")) +
  scale_y_discrete(labels = c("Very", "Somewhat", "Slightly", "Not at all")) +
  coord_fixed()
heatmap_political_interest
ggsave("./figures/heatmap_political_interest_optimized.png", plot = heatmap_political_interest, width = 7, height = 7, units = "in", dpi = 300)



#discuss politics
discuss_politics_2016_confusion <- short_discuss_politics_2016 %>% filter(model == 'gpt.4o.mini')
discuss_politics_2016_confusion$discuss_politics <- factor(discuss_politics_2016_confusion$discuss_politics, levels=c(1,2))
discuss_politics_2016_confusion$gpt.4o.mini <- factor(discuss_politics_2016_confusion$gpt.4o.mini, levels=c(1,2))
discuss_politics_2016_conf_matrix <- confusionMatrix(discuss_politics_2016_confusion$gpt.4o.mini, discuss_politics_2016_confusion$discuss_politics)

discuss_politics_conf_table <- as.data.frame(discuss_politics_2016_conf_matrix$table)
colnames(discuss_politics_conf_table) <- c("GPT", "ANES", "Count")

discuss_politics_conf_table <- discuss_politics_conf_table %>%
  mutate(
    Percentage = round((Count /  sum(discuss_politics_conf_table$Count)) * 100, 2),
    Label = paste0(Count, "\n(", Percentage, "%)")
  )

heatmap_discuss_politics <- ggplot(discuss_politics_conf_table, aes(x = ANES, y = GPT, fill = Count)) +
  geom_tile(color = "gray", linewidth = 0.5) +
  geom_text(aes(label = Label), color = "black", size = 7, fontface = "bold") +
  scale_fill_gradient(low = "white", high = "#1f77b4", name = "Count") +
  theme_minimal(base_size = 14) +
  labs(
    title = "",
    x = "ANES",
    y = "GPT") +
  theme(
    legend.position = "none", 
    axis.title = element_text(size = 20),
    axis.text = element_text(size = 20),
    plot.caption = element_text(size = 20, hjust = 0),
  ) +
  scale_x_discrete(labels = c("Yes", "No")) +
  scale_y_discrete(labels = c("Yes", "No")) +
  coord_fixed()
heatmap_discuss_politics
ggsave("./figures/heatmap_discuss_politics_optimized.png", plot = heatmap_discuss_politics, width = 7, height = 7, units = "in", dpi = 300)



# attend church
attend_church_2020_confusion <- short_attend_church_2020 %>% filter(model == 'gpt.4o.mini')
attend_church_2020_confusion$attend_church <- factor(attend_church_2020_confusion$attend_church, levels=c(1,2))
attend_church_2020_confusion$gpt.4o.mini <- factor(attend_church_2020_confusion$gpt.4o.mini, levels=c(1,2))

attend_church_2020_conf_matrix <- confusionMatrix(attend_church_2020_confusion$gpt.4o.mini, attend_church_2020_confusion$attend_church)

attend_church_conf_table <- as.data.frame(attend_church_2020_conf_matrix$table)
colnames(attend_church_conf_table) <- c("GPT", "ANES", "Count")

attend_church_conf_table <- attend_church_conf_table %>%
  mutate(
    Percentage = round((Count /  sum(attend_church_conf_table$Count)) * 100, 2),
    Label = paste0(Count, "\n(", Percentage, "%)")
  )

heatmap_attend_church <- ggplot(attend_church_conf_table, aes(x = ANES, y = GPT, fill = Count)) +
  geom_tile(color = "gray", linewidth = 0.5) +
  geom_text(aes(label = Label), color = "black", size = 7, fontface = "bold") +
  scale_fill_gradient(low = "white", high = "#1f77b4", name = "Count") +
  theme_minimal(base_size = 14) +
  labs(
    title = "",
    x = "ANES",
    y = "GPT") +
  theme(
    legend.position = "none", 
    axis.title = element_text(size = 20),
    axis.text = element_text(size = 20),
    plot.caption = element_text(size = 20, hjust = 0),
  ) +
  scale_x_discrete(labels = c("Yes", "No")) +
  scale_y_discrete(labels = c("Yes", "No")) +
  coord_fixed()
heatmap_attend_church
ggsave("./figures/heatmap_attend_church_optimized.png", plot = heatmap_attend_church, width = 7, height = 7, units = "in", dpi = 300)

#Please see the replication files for Study 3 to create heat maps for Study 3 complete observations.


#load predictions made with 20 variables

#load all files and update file name
formal_names_long <- c("long_attend_church_2012", "long_discuss_politics_2012", 
                  "long_political_interest_2012", "long_attend_church_2016", 
                  "long_discuss_politics_2016", "long_political_interest_2016", 
                  "long_attend_church_2020", "long_discuss_politics_2020", 
                  "long_political_interest_2020")


csv_long <- list.files(path = ".", pattern = "^long.*\\.csv$", full.names = TRUE)
for (i in seq_along(csv_long)) {
  df <- read.csv(csv_long[i])
  df <- df[, !grepl("completion$", names(df))]
  assign(formal_names_long[i], df, envir = .GlobalEnv)
}

for (df_name in formal_names_long) {
  df <- get(df_name)
  predictions <- tail(names(df), 2)
  df[predictions] <- lapply(df[predictions], function(col) as.numeric(as.character(col)))
  df <- df[complete.cases(df[predictions]), ]
  if (grepl("long_attend_church|long_discuss_politics", df_name)) {
    df <- df[df[[predictions[1]]] %in% c(1, 2) & df[[predictions[2]]] %in% c(1, 2), ]
  } else if (grepl("long_political_interest", df_name)) {
    df <- df[df[[predictions[1]]] %in% 1:4 & df[[predictions[2]]] %in% 1:4, ]
  }
  
  assign(df_name, df, envir = .GlobalEnv)
}

metrics_long <- data.frame(
  target_var = character(),
  year = numeric(),
  model = character(),
  proportion = numeric(),
  kappa = numeric(),
  f1 = numeric(),
  ICC = numeric(),
  tetrachoric = numeric(),
  optimized = character()
)

for (df_name in formal_names_long) {
  models <- c("gpt.3.5.turbo", "gpt.4o.mini")
  df <- get(df_name)
  target_var <- names(df)[2]
  
  for (model in models) {
    df[[target_var]] <- as.factor(df[[target_var]])
    df[[model]] <- as.factor(df[[model]])
    
    cont_table <- table(df[[target_var]], df[[model]])
    proportion <- round(sum(diag(prop.table(cont_table))), 2)
    
    kappa <- round(cohen.kappa(cbind(df[[target_var]], df[[model]]))$kappa, 2)
    
    # Compute confusion matrix and F1 score
    conf_matrix <- confusionMatrix(df[[model]], df[[target_var]])
    per_class_metrics <- conf_matrix$byClass
    
    if (names(df)[2] != "political_interest") {
      f1 <- round(per_class_metrics["F1"], 2)
    } else {
      class_counts <- table(df[[target_var]])
      f1 <- tryCatch({
        # Fix row name mismatch ("Class: 1" vs "1")
        row_classes <- gsub("Class: ", "", rownames(per_class_metrics))
        common_classes <- intersect(row_classes, names(class_counts))
        
        f1_scores <- per_class_metrics[match(paste0("Class: ", common_classes), rownames(per_class_metrics)), "F1"]
        class_counts_used <- class_counts[common_classes]
        
        # Remove names to avoid misaligned multiplication
        names(f1_scores) <- NULL
        names(class_counts_used) <- NULL
        
        valid <- !is.na(f1_scores)
        round(sum(f1_scores[valid] * class_counts_used[valid]) / sum(class_counts_used[valid]), 2)
      }, error = function(e) {
        print(paste("F1 error at:", df_name, "Model:", model, "Error:", e$message))
        NA
      })
    }
    # Compute ICC using dynamic columns
    ICC <- round(min(ICC(cbind(df[[target_var]], df[[model]]))$results$ICC[4:6]), 2)
    
    # Compute tetrachoric correlation
    if (names(df)[2] != "political_interest") {
      tetrachoric <- round(tetrachoric(cbind(df[[target_var]], df[[model]]))$rho[2], digits = 2)
    } else {
      tetrachoric <- NA
    }
    
    # Append metrics to the data frame
    metrics_long <- rbind(metrics_long, data.frame(
      target_var = target_var,
      year = as.numeric(sub(".*_(\\d{4})$", "\\1", df_name)),
      model = model,
      proportion = proportion,
      kappa = kappa,
      f1 = f1,
      ICC = ICC,
      tetrachoric = tetrachoric,
      optimized = 'yes'
    ))
  }
}


metrics_short <- metrics_short %>% mutate(short_long='10 var')
metrics_long <- metrics_long %>% mutate(short_long='20 var')

metrics_compare <- rbind(metrics_short,metrics_long)


subset_for_graphing <- function(target_var_input, year_input) {
  if (target_var_input == 'political_interest') {
    df_temp <- metrics_compare %>%
      filter(target_var == target_var_input, year == year_input) %>%
      select(model, proportion, f1, kappa, ICC,short_long) %>%
      mutate(across(where(is.numeric), ~ replace(., is.na(.), NA))) %>%
      pivot_longer(cols = c(proportion, f1, kappa, ICC),
                   names_to = "metric",
                   values_to = "value")
  } else {
    df_temp <- metrics_compare %>%
      filter(target_var == target_var_input, year == year_input) %>%
      select(model, proportion, f1, kappa, ICC, tetrachoric,short_long) %>%
      mutate(across(where(is.numeric), ~ replace(., is.na(.), NA))) %>%
      pivot_longer(cols = c(proportion, f1, kappa,ICC,tetrachoric),
                   names_to = "metric",
                   values_to = "value")
  }
  if(year_input != 2016){
    df_temp$model <- factor(df_temp$model, levels = c("gpt.3.5.turbo","gpt.4o.mini"))
  }
  df_temp$model <- factor(df_temp$model, levels = c("gpt.3.5.turbo","gpt.4o.mini"))
  if(target_var_input == 'political_interest'){
    df_temp$metric <- factor(df_temp$metric, levels = c("proportion", "f1", "kappa", "ICC"))
  }
  df_temp$metric <- factor(df_temp$metric, levels = c("proportion", "f1", "kappa", "ICC",'tetrachoric'))
  df_temp$short_long <- factor(df_temp$short_long, levels = c("10 var",'20 var'))
  return(df_temp)
}

political_interest_2012 <- subset_for_graphing('political_interest',2012)
political_interest_2016 <- subset_for_graphing('political_interest',2016)
political_interest_2020 <- subset_for_graphing('political_interest',2020)


# Plot
annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(political_interest_2012$model)),
  x = 1.76,
  y = 0.645,
  label = "Year: 2012"
)
legend_labels <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(political_interest_2012$model)),
  x_tile = c(1.4, 1.4),          
  x_text = c(1.5, 1.5),          
  y = c(0.60, 0.54),             
  label = c("10 var", "20 var"),
  fill = c("10 var", "20 var")
)

pi_12 <- ggplot(political_interest_2012, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.7),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  geom_tile(
    data = legend_labels,
    aes(x = x_tile, y = y, fill = fill),
    width = 0.15,
    height = 0.025,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = legend_labels,
    aes(x = x_text, y = y, label = label),
    size = 6,
    hjust = 0,
    inherit.aes = FALSE
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_text(size = 20),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.68),breaks = seq(0,0.65,by=0.15))

pi_12
ggsave("./figures/political_interest_2012_comp.png", plot = pi_12, width = 13.7, height = 6.8, units = "in", dpi = 300)

#2016

annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(political_interest_2016$model)),
  x = 1.76,
  y = 0.59,
  label = "Year: 2016"
)
pi_16 <- ggplot(political_interest_2016, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.6),breaks = seq(0,0.6,by=0.1))

pi_16
ggsave("./figures/political_interest_2016_comp.png", plot = pi_16, width = 13.7, height = 6.8, units = "in", dpi = 300)


annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(political_interest_2020$model)),
  x = 1.96,
  y = 0.5,
  label = "Year: 2020"
)
pi_20 <- ggplot(political_interest_2020, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20,angle = 45, hjust = 1),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.5),breaks = seq(0,0.5,by=0.1))

pi_20
ggsave("./figures/political_interest_2020_comp.png", plot = pi_20, width = 13.7, height = 6.8, units = "in", dpi = 300)


##############political discussion##################
discuss_politics_2012 <- subset_for_graphing('discuss_politics',2012)
discuss_politics_2016 <- subset_for_graphing('discuss_politics',2016)
discuss_politics_2020 <- subset_for_graphing('discuss_politics',2020)

annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(discuss_politics_2012$model)),
  x = 4,
  y = 0.73,
  label = "Year: 2012"
)
legend_labels <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(discuss_politics_2012$model)),
  x_tile = c(3.5, 3.5),          
  x_text = c(3.6, 3.6),          
  y = c(0.69, 0.63),             
  label = c("10 var", "20 var"),
  fill = c("10 var", "20 var")
)

dp_12 <- ggplot(discuss_politics_2012, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.7),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  geom_tile(
    data = legend_labels,
    aes(x = x_tile, y = y, fill = fill),
    width = 0.15,
    height = 0.025,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = legend_labels,
    aes(x = x_text, y = y, label = label),
    size = 6,
    hjust = 0,
    inherit.aes = FALSE
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_text(size = 20),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(-0.05, 0.75),breaks = seq(-0.05,0.75,by=0.15))

dp_12
ggsave("./figures/discuss_politics_2012_comp.png", plot = dp_12, width = 13.7, height = 6.8, units = "in", dpi = 300)



#2016

annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(discuss_politics_2016$model)),
  x = 3.76,
  y = 0.84,
  label = "Year: 2016"
)
dp_16 <- ggplot(discuss_politics_2016, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(-0.4, 0.9),breaks = seq(-0.35,0.9,by=0.15))

dp_16
ggsave("./figures/discuss_politics_2016_comp.png", plot = dp_16, width = 13.7, height = 6.8, units = "in", dpi = 300)



annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(discuss_politics_2020$model)),
  x = 3.7,
  y = 0.8,
  label = "Year: 2020"
)
dp_20 <- ggplot(discuss_politics_2020, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20,angle = 45, hjust = 1),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(-0.42, 0.85),breaks = seq(-0.4,0.85,by=0.15))

dp_20
ggsave("./figures/discuss_politics_2020_comp.png", plot = dp_20, width = 13.7, height = 6.8, units = "in", dpi = 300)



##############religious service##################
attend_church_2012 <- subset_for_graphing('attend_church',2012)
attend_church_2016 <- subset_for_graphing('attend_church',2016)
attend_church_2020 <- subset_for_graphing('attend_church',2020)


annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(attend_church_2012$model)),
  x = 3.9,
  y = 0.74,
  label = "Year: 2012"
)
legend_labels <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(attend_church_2012$model)),
  x_tile = c(3.5, 3.5),          
  x_text = c(3.6, 3.6),          
  y = c(0.69, 0.63),             
  label = c("10 var", "20 var"),
  fill = c("10 var", "20 var")
)

ac_12 <- ggplot(attend_church_2012, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.7),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  geom_tile(
    data = legend_labels,
    aes(x = x_tile, y = y, fill = fill),
    width = 0.15,
    height = 0.025,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = legend_labels,
    aes(x = x_text, y = y, label = label),
    size = 6,
    hjust = 0,
    inherit.aes = FALSE
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_text(size = 20),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.75),breaks = seq(-0.05,0.75,by=0.15))

ac_12
ggsave("./figures/attend_church_2012_comp.png", plot = ac_12, width = 13.7, height = 6.8, units = "in", dpi = 300)



#2016

annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(attend_church_2016$model)),
  x = 3.76,
  y = 0.75,
  label = "Year: 2016"
)
ac_16 <- ggplot(attend_church_2016, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(0, 0.77),breaks = seq(0,0.77,by=0.15))

ac_16
ggsave("./figures/attend_church_2016_comp.png", plot = ac_16, width = 13.7, height = 6.8, units = "in", dpi = 300)



annotation_df <- data.frame(
  model = factor("gpt.3.5.turbo", levels = levels(attend_church_2020$model)),
  x = 3.7,
  y = 0.67,
  label = "Year: 2020"
)
ac_20 <- ggplot(attend_church_2020, aes(x = metric, y = value, fill = short_long)) +
  geom_bar(
    aes(x = metric, y = value, fill = short_long),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.8
  ) +
  geom_text(
    aes(label = sprintf("%.2f", value)),
    position = position_dodge(width = 0.9),
    vjust = -0.3,
    size = 7,
    color = "black"
  ) +
  geom_text(
    data = annotation_df,
    aes(x = x, y = y, label = label),
    inherit.aes = FALSE,
    size = 7,
    color = "black"
  ) +
  facet_wrap(~ model, nrow = 1) +
  scale_fill_manual(values = c("10 var" = "#00BFC4", "20 var" = "#F8766D")) +
  labs(title = "",
       x = "", y = "", fill = "Short_long") +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20,angle = 45, hjust = 1),
    legend.position = 'none',
    axis.text.y = element_text(size = 20),
    strip.text = element_blank(),
    panel.spacing.x = unit(0.8, "lines")
  ) +
  scale_y_continuous(limits = c(-0.25, 0.7),breaks = seq(-0.25,0.7,by=0.15))

ac_20
ggsave("./figures/attend_church_2020_comp.png", plot = ac_20, width = 13.7, height = 6.8, units = "in", dpi = 300)

