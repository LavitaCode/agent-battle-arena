var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

var live = app.MapGroup("/api/v1/live");

live.MapGet("/health", () => Results.Ok(new HealthResponse(
        Status: "ok",
        Mode: "live-3d",
        Service: "AgentBattleArena.Live.Api")))
    .WithName("LiveHealth")
    .WithOpenApi();

app.Run();

public sealed record HealthResponse(string Status, string Mode, string Service);

/// <summary>Marker for WebApplicationFactory in integration tests.</summary>
public partial class Program;
